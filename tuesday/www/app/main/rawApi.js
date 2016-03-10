
app.controller('RawApiController', function ($scope, $http, $location) {
    /************************************************************************************************
     * Properties
     */

    $scope.data = []
    $scope.limits = ['None', 10, 20, 25, 50, 100];

    /************************************************************************************************
     * Actions
     */

    $scope.refresh = function () {
        var params = {};
        if ($scope.limit != 'None')
            params.limit = $scope.limit;

        var url = $location.path();
        var query = $.param(params);
        if (query !== '') {
            url = url + '?' + query;
        }

        $location.url(url);
    };

    /************************************************************************************************
     * Methods
     */

    $scope.buildUrl = function () {
        url = 'http://' + $location.host() + ':' + $location.port() + '/api/v1' + $location.url()
        return url;
    };

    $scope.buildBreadcrumbs = function () {
        nodes = $location.path().split('/');

        result = [];
        currentPath = 'http://' + $location.host() + ':' + $location.port()

        angular.forEach(nodes, function (node) {
            if (node !== '') {
                currentPath = currentPath + '/' + node;
                result.push({ 'name': node, 'link': currentPath });
            }
        });

        return result;
    };

    $scope.initOptions = function () {
        var query = $location.search();

        $scope.limit = ('limit' in query) ? parseInt(query['limit']) : 'None';
    };

    /************************************************************************************************
     * Initialization
     */

    $scope.initOptions();

    $scope.apiUrl = $scope.buildUrl();
    crumbs = $scope.buildBreadcrumbs();
    $scope.activeNode = crumbs.slice(-1)[0];
    $scope.breadcrumbs = crumbs.slice(0, -1);

    $http.get(url).then(
        function (response) { $scope.data = response.data; },
        function (response) { alert(response.status) }
        );
});