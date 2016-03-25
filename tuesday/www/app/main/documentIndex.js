
app.controller('DocumentIndexController', function ($scope, $http, $location) {
    /************************************************************************************************
     * Properties
     */

    $scope.model = []
    $scope.columns = [
        { 'name': 'title', 'title': 'Title', 'show': true, 'type': 'string' },
        { 'name': 'author', 'title': 'Author(s)', 'show': true, 'type': 'string' },
        { 'name': 'updated', 'title': 'Scanned', 'show': true, 'type': 'date' },
        { 'name': 'source', 'title': 'Source', 'show': true, 'type': 'string' },
        { 'name': 'type', 'title': 'Type', 'show': true, 'type': 'string' }
    ]

    $scope.limits = ['None', 100, 200, 500, 1000];

    $scope.searchText = '';

    /************************************************************************************************
     * Synching URL and params
     */

    $scope.initOptions = function () {
        var query = $location.search();

        $scope.limit = ('limit' in query) ? parseInt(query['limit']) : 'None';
        $scope.searchText = ('filter' in query) ? query['filter'] : '';
    };

    $scope.addParams = function (baseUrl) {
        var params = {};
        if ($scope.limit != 'None')
            params.limit = $scope.limit;
        if ($scope.searchText !== '')
            params.filter = $scope.searchText;

        var url = baseUrl;
        var query = $.param(params);
        if (query !== '') {
            url = url + '?' + query;
        }

        return url;
    };

    $scope.buildUrl = function () {
        return $scope.addParams($location.path());
    };

    $scope.buildApiUrl = function () {
        var url = 'http://' + $location.host() + ':' + $location.port() + '/api/v1/document'
        return $scope.addParams(url);
    };

    /************************************************************************************************
    * Data Model Methods
    */

    $scope.refresh = function () {
        $scope.loading = true;

        $location.url($scope.buildUrl());
    };

    $scope.onModelLoaded = function (data) {
        $scope.loading = false;

        $scope.model = data;
        if ($scope.model == null) {
            $scope.model = [];
            return;
        }

        // Initialize the columns
        angular.forEach($scope.model, function (row) {
            // Fix up the 'updated' column
            if ("updated" in row) {
                row["updated"] = new Date(row["updated"]).toLocaleString();
            }

            if ("links" in row) {
                // Pop the 'View/Edit' link as the primary
                var elem = row["links"].shift();
                row["view"] = elem.href.replace('/api/v1/', '/');

                // Fix the urls
                angular.forEach(row["links"], function (link) {
                    link.href = link.href.replace('/api/v1/', '/');
                });
            }
        });

        angular.forEach($scope.columns, function (column) {
            if ($scope.orderBy == undefined && column.show) {
                $scope.orderBy = column.name;
            }
        });

        $scope.showNavigation = ($scope.model.length > 20);

        // Initialize the pagination data
        $scope.initializePages();
    }

    /************************************************************************************************
     * Table Members
     */

    $scope.orderBy = undefined;
    $scope.totalItems = 0;
    $scope.pageSize = 20
    $scope.currentPage = 1;
    $scope.offset = 0;
    $scope.lastShown = 0;
    $scope.showPagination = true;

    $scope.initializePages = function () {
        $scope.totalItems = $scope.model.length;
        $scope.showPagination = ($scope.totalItems >= 20);
        $scope.currentPage = 1;
        $scope.pageChanged();
    }

    $scope.pageChanged = function () {
        $scope.offset = ($scope.currentPage - 1) * $scope.pageSize
        $scope.lastShown = Math.min($scope.offset + $scope.pageSize + 1, $scope.totalItems);
    };

    $scope.setOrder = function (orderBy) {
        if (orderBy === $scope.orderBy)
            $scope.orderBy = '-' + orderBy;  // Reverse the sort
        else
            $scope.orderBy = orderBy;
    }

    /************************************************************************************************
     * Initialization
     */

    $scope.initOptions();

    $scope.$watch('searchText', function (term) {
        $scope.refresh();
    });

    $http.get($scope.buildApiUrl()).then(
        function (response) { $scope.onModelLoaded(response.data); },
        function (response) { alert(response.status) }
        );
});